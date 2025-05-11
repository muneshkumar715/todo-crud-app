document.addEventListener('DOMContentLoaded', () => {
    const taskInput = document.getElementById('taskInput');
    const addTaskBtn = document.getElementById('addTaskBtn');
    const taskList = document.getElementById('taskList');
    const editModal = document.getElementById('editModal');
    const editTaskInput = document.getElementById('editTaskInput');
    const saveEditBtn = document.getElementById('saveEditBtn');
    const cancelEditBtn = document.getElementById('cancelEditBtn');
    let currentEditId = null;

    const fetchTasks = async () => {
        try {
            const response = await fetch('/api/tasks');
            if (!response.ok) throw new Error('Failed to fetch tasks');
            const tasks = await response.json();
            taskList.innerHTML = '';
            tasks.forEach(task => {
                const taskItem = document.createElement('div');
                taskItem.className = 'flex items-center justify-between p-3 bg-gray-50 rounded-lg fade-in';
                taskItem.innerHTML = `
                    <span class="text-gray-800">${task.task}</span>
                    <div class="space-x-2">
                        <button class="edit-btn bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600" data-id="${task.id}">Edit</button>
                        <button class="delete-btn bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600" data-id="${task.id}">Delete</button>
                    </div>
                `;
                taskList.appendChild(taskItem);
            });
        } catch (error) {
            console.error('Error fetching tasks:', error);
            taskList.innerHTML = '<p class="text-red-500">Error loading tasks</p>';
        }
    };

    const addTask = async () => {
        const task = taskInput.value.trim();
        if (!task) {
            alert('Please enter a task');
            return;
        }
        try {
            const response = await fetch('/api/tasks', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ task })
            });
            if (!response.ok) throw new Error('Failed to add task');
            taskInput.value = '';
            fetchTasks();
        } catch (error) {
            console.error('Error adding task:', error);
            alert('Error adding task');
        }
    };

    const editTask = async (id, task) => {
        try {
            const response = await fetch(`/api/tasks/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ task })
            });
            if (!response.ok) throw new Error('Failed to update task');
            fetchTasks();
        } catch (error) {
            console.error('Error updating task:', error);
            alert('Error updating task');
        }
    };

    const deleteTask = async (id) => {
        if (!confirm('Are you sure you want to delete this task?')) return;
        try {
            const response = await fetch(`/api/tasks/${id}`, {
                method: 'DELETE'
            });
            if (!response.ok) throw new Error('Failed to delete task');
            fetchTasks();
        } catch (error) {
            console.error('Error deleting task:', error);
            alert('Error deleting task');
        }
    };

    addTaskBtn.addEventListener('click', addTask);
    taskInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') addTask();
    });

    taskList.addEventListener('click', (e) => {
        if (e.target.classList.contains('edit-btn')) {
            currentEditId = e.target.dataset.id;
            editTaskInput.value = e.target.parentElement.previousElementSibling.textContent;
            editModal.classList.remove('hidden');
        } else if (e.target.classList.contains('delete-btn')) {
            deleteTask(e.target.dataset.id);
        }
    });

    saveEditBtn.addEventListener('click', () => {
        const task = editTaskInput.value.trim();
        if (!task) {
            alert('Please enter a task');
            return;
        }
        editTask(currentEditId, task);
        editModal.classList.add('hidden');
    });

    cancelEditBtn.addEventListener('click', () => {
        editModal.classList.add('hidden');
        currentEditId = null;
    });

    fetchTasks();
});