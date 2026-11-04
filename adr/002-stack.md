# ADR-002: Stack layout

I decided to separare the network and application. Since the app costs money and we have only 50 dollars in credit, I would have to delete the app after sessions. If i separate them I can keep the network and delete only the application. Also, if I break the application I can only roll back the broken part and keep the network untouched.

## Consequences

− Changing the network later takes extra steps, because you must delete the server stack first.
