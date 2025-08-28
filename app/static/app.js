const api = {
  chat: '/api/chat',
  todos: '/api/todos',
  reminders: '/api/reminders',
  notifications: '/api/notifications',
};

// Chat
const chatLog = document.getElementById('chat-log');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
let chatHistory = [{ role: 'system', content: 'You are a helpful assistant.' }];

function addChat(role, content) {
  const div = document.createElement('div');
  div.className = `chat-msg role-${role}`;
  div.textContent = `${role === 'user' ? 'You' : 'Assistant'}: ${content}`;
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight;
}

chatForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const text = chatInput.value.trim();
  if (!text) return;
  chatInput.value = '';
  addChat('user', text);
  chatHistory.push({ role: 'user', content: text });
  const res = await fetch(api.chat, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages: chatHistory }),
  });
  const data = await res.json();
  addChat('assistant', data.reply);
  chatHistory.push({ role: 'assistant', content: data.reply });
});

// Todos
const todoForm = document.getElementById('todo-form');
const todoTitle = document.getElementById('todo-title');
const todoDue = document.getElementById('todo-due');
const todoList = document.getElementById('todo-list');

async function loadTodos() {
  const res = await fetch(api.todos);
  const data = await res.json();
  todoList.innerHTML = '';
  data.forEach((t) => {
    const li = document.createElement('li');
    const cb = document.createElement('input');
    cb.type = 'checkbox';
    cb.checked = t.completed;
    cb.addEventListener('change', async () => {
      await fetch(`${api.todos}/${t.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ completed: cb.checked }),
      });
      loadTodos();
    });
    const span = document.createElement('span');
    span.className = 'flex';
    span.textContent = t.title;
    const meta = document.createElement('span');
    meta.className = 'small';
    meta.textContent = t.due_at ? `due ${new Date(t.due_at).toLocaleString()}` : '';
    const del = document.createElement('button');
    del.textContent = 'Delete';
    del.addEventListener('click', async () => {
      await fetch(`${api.todos}/${t.id}`, { method: 'DELETE' });
      loadTodos();
    });
    li.append(cb, span, meta, del);
    todoList.appendChild(li);
  });
}

todoForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const title = todoTitle.value.trim();
  if (!title) return;
  await fetch(api.todos, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, due_at: todoDue.value ? new Date(todoDue.value).toISOString() : null }),
  });
  todoTitle.value = '';
  todoDue.value = '';
  loadTodos();
});

// Reminders
const reminderForm = document.getElementById('reminder-form');
const reminderText = document.getElementById('reminder-text');
const reminderDue = document.getElementById('reminder-due');
const reminderList = document.getElementById('reminder-list');
const notifList = document.getElementById('notification-list');

async function loadReminders() {
  const res = await fetch(api.reminders);
  const data = await res.json();
  reminderList.innerHTML = '';
  data.forEach((r) => {
    const li = document.createElement('li');
    const span = document.createElement('span');
    span.className = 'flex';
    span.textContent = r.text;
    const meta = document.createElement('span');
    meta.className = 'small';
    meta.textContent = `${new Date(r.due_at).toLocaleString()}${r.completed ? ' (done)' : ''}`;
    const del = document.createElement('button');
    del.textContent = 'Delete';
    del.addEventListener('click', async () => {
      await fetch(`${api.reminders}/${r.id}`, { method: 'DELETE' });
      loadReminders();
    });
    li.append(span, meta, del);
    reminderList.appendChild(li);
  });
}

async function loadNotifications() {
  const res = await fetch(api.notifications);
  const data = await res.json();
  notifList.innerHTML = '';
  data.forEach((n) => {
    const li = document.createElement('li');
    li.textContent = `${new Date(n.fired_at).toLocaleTimeString()}: ${n.text}`;
    notifList.appendChild(li);
  });
}

reminderForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const text = reminderText.value.trim();
  const due = reminderDue.value;
  if (!text || !due) return;
  await fetch(api.reminders, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, due_at: new Date(due).toISOString() }),
  });
  reminderText.value = '';
  reminderDue.value = '';
  loadReminders();
});

function refreshAll() {
  loadTodos();
  loadReminders();
  loadNotifications();
}

refreshAll();
setInterval(loadNotifications, 5000);

