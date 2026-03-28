// ================== LOGIN ==================
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const formData = new FormData(loginForm);
        const payload = new URLSearchParams();
        for (const [key, value] of formData.entries()) {
            payload.append(key, value);
        }

        try {
            const response = await fetch('/auth/token', {
                method: 'POST',
                body: payload.toString(),
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                credentials: 'include' // <- envía la cookie automáticamente
            });

            if (response.redirected) {
                window.location.href = response.url;
            } else {
                const data = await response.json();
                alert(`Error: ${data.detail}`);
            }
        } catch (err) {
            console.error('Error:', err);
            alert('An error occurred. Please try again.');
        }
    });
}

// ================== REGISTER ==================
const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', async function (event) {
        event.preventDefault();
        const formData = new FormData(registerForm);
        const data = Object.fromEntries(formData.entries());

        if (data.password !== data.password2) {
            alert("Passwords do not match");
            return;
        }

        const payload = {
            email: data.email,
            username: data.username,
            first_name: data.firstname,
            last_name: data.lastname,
            role: data.role,
            phone_number: data.phone_number,
            password: data.password
        };

        try {
            const response = await fetch('/auth', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                window.location.href = '/auth/login-page';
            } else {
                let errorMsg = "Unknown error";

                try {
                    const errorData = await response.json();
                    errorMsg = errorData.detail || errorData.message;
                } catch {
                    errorMsg = await response.text();
                }

                console.error(errorMsg);
                alert(`Error: ${errorMsg}`);
            }
        }
    )
        ;
    }

// Add Todo
    const todoForm = document.getElementById('todoForm');

    if (todoForm) {
        todoForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const data = Object.fromEntries(new FormData(todoForm).entries());

            const payload = {
                title: data.title,
                description: data.description,
                priority: parseInt(data.priority),
                complete: false
            };

            try {
                const response = await fetch('/todos/todo', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload),
                    credentials: 'include'
                });

                if (response.ok) {
                    document.getElementById('todoForm')?.reset();
                    window.location.href = '/todos/todo-page';
                } else {
                    const text = await response.text();
                    console.error(text);
                    alert('Error creando todo');
                }
            } catch (err) {
                console.error('Error:', err);
            }
        });
    }

// Edit Todo
    const editTodoForm = document.getElementById('editTodoForm');

    if (editTodoForm) {
        editTodoForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const data = Object.fromEntries(new FormData(editTodoForm).entries());
            const todoId = window.location.pathname.split("/").pop();

            const payload = {
                title: data.title,
                description: data.description,
                priority: parseInt(data.priority),
                complete: data.complete === "on"
            };

            try {
                const response = await fetch(`/todos/todo/${todoId}`, {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload),
                    credentials: 'include'
                });

                if (response.ok) {
                    editTodoForm.reset(); // ✅ evitar usar "form"
                    window.location.href = '/todos/todo-page';
                } else {
                    const text = await response.text();
                    console.error(text);
                    alert('Error actualizando todo');
                }
            } catch (err) {
                console.error('Error:', err);
            }
        });
    }


// ================== DELETE ==================
    const deleteButton = document.getElementById('deleteButton');

    if (deleteButton) {
        deleteButton.addEventListener('click', async () => {

            const todoId = window.location.pathname.split("/").pop();


            try {
                const response = await fetch(`/todos/todo/${todoId}`, {
                    method: 'DELETE',
                    credentials: 'include'
                });

                if (response.ok) {
                    window.location.href = '/todos/todo-page';
                } else {
                    const text = await response.text();
                    console.error(text);
                    alert('Error eliminando todo');
                }
            } catch (err) {
                console.error('Error:', err);
                alert('An error occurred.');
            }
        });
    }

// ================== LOGOUT ==================
    function logout() {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            const eqPos = cookie.indexOf("=");
            const name = eqPos > -1 ? cookie.substr(0, eqPos).trim() : cookie.trim();
            document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/";
        }
        window.location.href = '/auth/login-page';
    }