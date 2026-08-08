# A Practical Guide to Testing Your Django API (instead of Postman)

This walks through *how* the tests I've been writing for you actually work, so you can
write the next ones yourself — for Listings, and anything you build after this project.

---

## 1. The one setup fix you need right now

Open `core/settings.py` and look at this:

```python
DATABASES = {
    'default': {},
    'users': { ... },
    'listings': { ... },
}
```

`'default'` is empty. That's fine for your app running normally (your routers send
everything to `users`/`listings`), but Django's test runner tries to create a *test
version* of every database listed in `DATABASES` — including `default` — before it runs
a single test. An empty dict has no `ENGINE`, so it errors out immediately.

You don't need to solve your Postgres routing to fix this. Just give `default` a
throwaway engine:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    'users': { ... },      # leave as-is
    'listings': { ... },   # leave as-is
}
```

This doesn't affect your real app behavior at all — `default` is never actually queried
because your routers intercept everything for the `user` and `listing` apps. It just
gives the test runner something valid to spin up. Do this once and move on.

---

## 2. Where test files live

Django's convention: each app gets its own `tests.py` (or a `tests/` folder if it grows
large). You already have the right files:

```
user/tests.py
listing/tests.py
```

Django auto-discovers any file matching `test*.py` under each installed app when you run
`manage.py test`. You don't need to register them anywhere.

---

## 3. Anatomy of a test file

Here's the skeleton every test file follows:

```python
from rest_framework import status
from rest_framework.test import APITestCase

class RegisterViewTests(APITestCase):        # 1. a class per "feature" or view
    databases = {"default", "users"}          # 2. which DB aliases this class touches

    def setUp(self):                          # 3. runs before EVERY test method below
        ...

    def test_register_regular_user_success(self):   # 4. one method per scenario
        response = self.client.post(...)             # 5. make the request
        self.assertEqual(response.status_code, 201)   # 6. check the result
```

**Piece by piece:**

- **`APITestCase`** — DRF's test base class. Gives you `self.client`, an API client that
  works like Postman but lives in Python. Use it instead of plain Django `TestCase` for
  anything hitting a DRF view.
- **`databases = {...}`** — because your project uses custom routers (`AuthRouter`,
  `ListingRouter`), Django needs you to explicitly say which DB aliases a test class is
  allowed to touch. Forget this and you'll get a `DatabaseOperationForbidden` error the
  moment your code tries to save a `User` or `Listing`. Rule of thumb: if the test
  creates a `User`, include `"users"`. If it creates a `Listing`, include `"listings"`.
  `"default"` is always safe to include too.
- **`setUp`** — optional. Anything here runs fresh before *each* `test_...` method. Good
  for "create a user I'll need in several tests below."
- **`test_...` methods** — this is the actual unit of a test. **The method name must
  start with `test_`** or Django won't run it. Name it after the scenario, not the
  endpoint — `test_register_fails_on_password_mismatch` tells you what broke just from
  the test name in the output.

---

## 4. Making requests — the Postman-to-Python translation

| In Postman you... | In a test you... |
|---|---|
| Pick POST/GET and paste a URL | `self.client.post("/auth/user/register")` / `self.client.get(...)` |
| Set Body → raw → JSON | pass a dict as the second argument, `format="json"` |
| Set Body → form-data (for file uploads) | pass a dict, `format="multipart"` |
| Add an Authorization header with a Bearer token | `self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")` — set once, applies to every request after |
| Click Send and read the response | the return value: `response.status_code`, `response.data` |

Example, directly mirroring your "Register Normal Account" Postman request:

```python
response = self.client.post(
    "/auth/user/register",
    {
        "name": "Jon Doe",
        "email": "jonedoe@gmail.com",
        "password": "password",
        "re_password": "password",
        "is_realtor": "False",
    },
    format="json",
)
self.assertEqual(response.status_code, status.HTTP_201_CREATED)
```

That's it — that's your Postman tab, as code.

**For endpoints needing a file upload** (your `manage` listing-create endpoint needs 4
images), use `format="multipart"` and build fake image bytes with
`SimpleUploadedFile` — see the `make_image()` helper in `listing_tests.py` for a
reusable pattern.

---

## 5. Handling JWT auth in tests

Two ways to get a token in a test, both valid:

**A) Go through the real login endpoint** (closer to what a real client does):
```python
token_response = self.client.post(
    "/api/token/", {"email": user.email, "password": "password123"}, format="json"
)
access_token = token_response.data["access"]
self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
```

**B) Shortcut straight to a token** (faster, skips hitting the login view — useful when
the test isn't *about* login, e.g. testing the listing-create endpoint):
```python
from rest_framework_simplejwt.tokens import RefreshToken

token = RefreshToken.for_user(user).access_token
self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
```

Use (A) when you're specifically testing login/auth behavior. Use (B) everywhere else,
so the test stays focused on the thing it's actually checking.

---

## 6. Assertions — the "checks" you'll use most

```python
self.assertEqual(response.status_code, status.HTTP_200_OK)   # exact match
self.assertIn("access", response.data)                       # key exists in response
self.assertTrue(user.is_realtor)                              # value is truthy
self.assertFalse(User.objects.filter(email=...).exists())     # nothing got created
```

Reading DRF status codes as words (`status.HTTP_404_NOT_FOUND` instead of `404`) makes
failures easier to read later — worth doing even though it's more typing.

---

## 7. Running your tests

```bash
python manage.py test                    # everything
python manage.py test user               # just the user app
python manage.py test listing            # just the listing app
python manage.py test user.tests.RegisterViewTests                       # one class
python manage.py test user.tests.RegisterViewTests.test_register_realtor_success  # one test
python manage.py test -v 2               # verbose: prints each test name as it runs
```

Run the specific test you're working on while you write it (fast feedback), then run the
whole suite before you consider a feature "done."

---

## 8. Why you can run these over and over without cleanup

This was your question last time, worth repeating here: every `TestCase` wraps each
`test_...` method in a database transaction that gets **rolled back** the instant that
method finishes. On top of that, the entire test database is destroyed and rebuilt from
scratch every time you run `manage.py test`. So "Jon Doe" from your register test never
persists anywhere — run it 100 times, it passes 100 times. This is the opposite of
Postman, where a second run of "Register Normal Account" fails because the email's
already taken from the first run.

Your **real** dev database (the one you look at in pgAdmin / Postman hits) is completely
untouched by any of this — tests run against a separate, temporary database that only
exists while `manage.py test` is running.

---

## 9. A workflow for converting the rest of your Postman collection

For each Postman request you want to turn into a test:

1. **Name the scenario**, not the endpoint — "creating a listing with a taken slug
   should fail" rather than "test manage post". That name becomes your method name.
2. **Copy the body** from Postman into the test almost verbatim, as a Python dict.
3. **Decide what "success" means** — usually a status code, sometimes also "did the
   right thing show up in the database" (`Listing.objects.filter(...).exists()`).
4. **Write the sad-path too** — for every "should work" test, ask "what should reject
   this?" (missing auth, wrong role, bad data) and write that as a second test. This is
   usually where you find bugs, like the inverted `.exists()` check we found in
   `ManageListingView.get()`.
5. **Run it.** If it fails and you expected it to pass, you either wrote the test wrong
   or found a real bug — both are useful to know.

---

## 10. Next: Listings

Send over the Listings Postman screenshots (get-listings, detail, manage) when you're
ready, and we'll walk through building those the same way — this time you can try
writing a first draft yourself using this guide, and I'll check it against the real
code like I did here.
