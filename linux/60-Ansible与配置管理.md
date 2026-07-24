# 60 - Ansible 与配置管理

> 管理一台服务器用 SSH，管理十台服务器用脚本，管理一百台服务器就需要配置管理工具。Ansible 以其无 Agent（仅需 SSH）、YAML 语法（易读易写）和丰富的模块生态成为最流行的配置管理方案之一。本章从 Inventory 和 Playbook 起步，到 Roles 和 Ansible Vault，构建可复用的自动化运维能力。

---

## 60.1 为什么需要配置管理

### 手动运维的困境

```bash
# 场景：给 50 台服务器装 Nginx
# 手动方式：
for host in $(cat hosts.txt); do
    ssh $host "sudo apt update && sudo apt install -y nginx &&
               sudo systemctl enable --now nginx"
done

# 问题：
# - 某台机器死活装不上，排查困难
# - 不同发行版命令不同（apt vs dnf vs pacman）
# - 配置文件需要模板化（不同环境不同值）
# - 不能确保幂等性（重复执行可能报错）
# - 没有变更记录和审计
```

### 配置管理工具对比

| 特性 | Ansible | Puppet | Chef | Salt |
|------|---------|--------|------|------|
| 架构 | 无 Agent（SSH） | Agent-Server | Agent-Server | Agent-Server |
| 配置语言 | YAML | 自定义 DSL | Ruby DSL | YAML |
| 学习曲线 | 低 | 高 | 中高 | 中 |
| 速度 | 中等 | 快（有 Agent） | 快 | 最快 |
| 推送模式 | Push | Pull | Pull | Push + Pull |
| 社区规模 | 最活跃 | 成熟 | 成熟 | 活跃 |

**Ansible 的核心优势**：无 Agent、YAML 易读、模块覆盖广、适合中小型团队和混合环境。

---

## 60.2 安装 Ansible

```bash
# Debian / Ubuntu
sudo apt install ansible -y

# RHEL / Fedora（可能需要 EPEL）
sudo dnf install epel-release -y
sudo dnf install ansible -y

# Arch
sudo pacman -S ansible

# macOS
brew install ansible

# 使用 pip（跨发行版，版本最新）
pip install ansible

# 验证
ansible --version
```

> 注意：Ansible 只需要在**控制节点（操控机）**安装，被管理的目标机只需有 Python 和 SSH。

---

## 60.3 Inventory（主机清单）

### 静态 Inventory

```bash
mkdir -p ~/ansible
vim ~/ansible/inventory.ini
```

```ini
# 单个主机
web-server-01 ansible_host=192.168.1.10 ansible_user=deploy

# 主机组
[webservers]
web-01 ansible_host=192.168.1.10
web-02 ansible_host=192.168.1.11
web-03 ansible_host=192.168.1.12

[databases]
db-01 ansible_host=192.168.1.20
db-02 ansible_host=192.168.1.21

# 组嵌套
[production:children]
webservers
databases

# 组变量
[webservers:vars]
ansible_user=deploy
ansible_ssh_private_key_file=~/.ssh/id_ed25519
http_port=80
```

### 动态 Inventory

```bash
# AWS EC2 动态 Inventory
pip install boto3
ansible-inventory -i aws_ec2.yml --list

# 或使用插件
vim ~/ansible/aws_ec2.yml
```

```yaml
plugin: aws_ec2
regions:
  - us-east-1
  - us-west-2
keyed_groups:
  - key: tags.Role
    prefix: role_
  - key: tags.Env
    prefix: env_
```

### 测试连接

```bash
# Ping 所有主机
ansible all -i inventory.ini -m ping

# 列出所有主机
ansible all -i inventory.ini --list-hosts

# 针对特定组
ansible webservers -i inventory.ini -m ping
```

---

## 60.4 Ad-Hoc 命令

在没有 Playbook 时，Ansible 可以像并行 SSH 一样使用：

```bash
# 语法：ansible <host-pattern> -i <inventory> -m <module> -a <args>

# 执行 Shell 命令
ansible webservers -i inventory.ini -m shell -a "uname -a"
ansible all -i inventory.ini -m shell -a "df -h /"

# 安装软件
ansible webservers -i inventory.ini -m apt -a "name=nginx state=present" --become
ansible databases -i inventory.ini -m dnf -a "name=mariadb-server state=present" --become
ansible arch_servers -i inventory.ini -m pacman -a "name=nginx state=present" --become

# 管理服务
ansible webservers -i inventory.ini -m systemd -a "name=nginx state=restarted" --become

# 复制文件
ansible webservers -i inventory.ini -m copy -a "src=./index.html dest=/var/www/html/index.html owner=www-data" --become

# 获取事实
ansible web-01 -i inventory.ini -m setup | less

# 获取特定事实
ansible web-01 -i inventory.ini -m setup -a "filter=ansible_distribution"
ansible web-01 -i inventory.ini -m setup -a "filter=ansible_memory_mb"
```

### 常用参数

```bash
--become             # 提权（sudo）
--become-user=root   # 提权目标用户
--limit              # 限制执行范围
--forks 10           # 并行数量
--check              # 预演模式（dry-run）
--diff               # 显示变更差异
-v / -vv / -vvv      # 增加输出详细度
```

---

## 60.5 Playbook

Playbook 是 Ansible 的核心，用 YAML 定义一系列任务。

### 基础 Playbook

```yaml
# playbook.yml
---
- name: Configure Web Server
  hosts: webservers
  become: yes

  tasks:
    - name: Install Nginx
      apt:
        name: nginx
        state: present
        update_cache: yes
      when: ansible_os_family == "Debian"

    - name: Install Nginx (RHEL)
      dnf:
        name: nginx
        state: present
      when: ansible_os_family == "RedHat"

    - name: Copy Nginx config
      template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
        owner: root
        group: root
        mode: '0644'
      notify: Reload Nginx

    - name: Ensure Nginx is running
      systemd:
        name: nginx
        state: started
        enabled: yes

    - name: Open firewall port
      ufw:
        rule: allow
        port: '80'
        proto: tcp
      when: ansible_os_family == "Debian"

  handlers:
    - name: Reload Nginx
      systemd:
        name: nginx
        state: reloaded
```

```bash
# 执行 Playbook
ansible-playbook -i inventory.ini playbook.yml

# Dry run（预演，不实际执行）
ansible-playbook -i inventory.ini playbook.yml --check --diff

# 从指定任务开始执行
ansible-playbook -i inventory.ini playbook.yml --start-at-task="Copy Nginx config"

# 指定 tag
ansible-playbook -i inventory.ini playbook.yml --tags "nginx,firewall"
ansible-playbook -i inventory.ini playbook.yml --skip-tags "slow"
```

### Handlers

Handler 只在被 `notify` 时才执行，且只在所有 Task 完成后执行一次（幂等）。

```yaml
tasks:
  - name: Update Nginx config
    template:
      src: nginx.conf.j2
      dest: /etc/nginx/nginx.conf
    notify:
      - Test Nginx config
      - Reload Nginx

handlers:
  - name: Test Nginx config
    command: nginx -t

  - name: Reload Nginx
    systemd:
      name: nginx
      state: reloaded
```

### 变量（Vars）

```yaml
---
- name: Deploy Application
  hosts: webservers
  vars:
    app_name: myapp
    app_version: "1.2.3"
    app_port: 8080

  tasks:
    - name: Create app directory
      file:
        path: "/opt/{{ app_name }}"
        state: directory
        mode: '0755'

    - name: Deploy app binary
      copy:
        src: "files/{{ app_name }}-{{ app_version }}.jar"
        dest: "/opt/{{ app_name }}/app.jar"
```

### 变量优先级（从低到高）

1. Role defaults
2. Inventory `group_vars/all`
3. Inventory `group_vars/<group>`
4. Inventory `host_vars/<host>`
5. Playbook `vars`
6. Playbook `vars_files`
7. `--extra-vars` 命令行传入（最高）

```bash
ansible-playbook playbook.yml -e "app_version=2.0.0 deploy_env=prod"
```

### Jinja2 模板

```yaml
# templates/nginx.conf.j2
server {
    listen {{ http_port | default(80) }};
    server_name {{ server_name }};

    root /var/www/{{ app_name }};

    location / {
        proxy_pass http://127.0.0.1:{{ app_port }};

        {% if enable_gzip %}
        gzip on;
        gzip_types text/plain application/json;
        {% endif %}
    }

    {% for backend in upstream_servers %}
    # backend: {{ backend }}
    {% endfor %}
}
```

### 条件与循环

```yaml
tasks:
  # 条件
  - name: Install only on Debian
    apt:
      name: nginx
    when: ansible_os_family == "Debian"

  - name: Install only on RHEL 8+
    dnf:
      name: nginx
    when:
      - ansible_os_family == "RedHat"
      - ansible_distribution_major_version | int >= 8

  - name: Only if file doesn't exist
    command: /usr/local/bin/init-db
    args:
      creates: /var/lib/myapp/.initialized

  # 循环
  - name: Install multiple packages
    apt:
      name: "{{ item }}"
      state: present
    loop:
      - nginx
      - htop
      - git
      - vim

  - name: Create multiple users
    user:
      name: "{{ item.name }}"
      groups: "{{ item.groups | default('') }}"
      shell: /bin/bash
      state: present
    loop:
      - { name: 'alice', groups: 'docker,sudo' }
      - { name: 'bob', groups: 'developers' }

  - name: Open multiple ports
    ufw:
      rule: allow
      port: "{{ item }}"
      proto: tcp
    loop:
      - 22
      - 80
      - 443
```

---

## 60.6 Roles

Role 是 Ansible 的组织单元，将变量、任务、模板、文件等归类。

### Role 目录结构

```
roles/
└── nginx/
    ├── defaults/         # 默认变量（最低优先级）
    │   └── main.yml
    ├── vars/             # 高优先级变量
    │   └── main.yml
    ├── tasks/            # 任务列表
    │   └── main.yml
    ├── handlers/         # Handler
    │   └── main.yml
    ├── templates/        # Jinja2 模板
    │   └── nginx.conf.j2
    ├── files/            # 静态文件（copy 模块使用）
    │   └── index.html
    ├── meta/             # Role 依赖和元信息
    │   └── main.yml
    └── README.md
```

### Role 示例：nginx

**`roles/nginx/defaults/main.yml`：**

```yaml
nginx_port: 80
nginx_server_name: localhost
nginx_root: /var/www/html
nginx_user: www-data        # RHEL 覆盖为 nginx
enable_https: false
```

**`roles/nginx/tasks/main.yml`：**

```yaml
---
- name: Install Nginx (Debian)
  apt:
    name: nginx
    state: present
    update_cache: yes
  when: ansible_os_family == "Debian"
  tags: [nginx, install]

- name: Install Nginx (RHEL)
  dnf:
    name: nginx
    state: present
  when: ansible_os_family == "RedHat"
  tags: [nginx, install]

- name: Deploy config
  template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    owner: root
    group: root
    mode: '0644'
    validate: '/usr/sbin/nginx -t -c %s'
  notify: Reload Nginx
  tags: [nginx, config]

- name: Create web root
  file:
    path: "{{ nginx_root }}"
    state: directory
    mode: '0755'
    owner: "{{ nginx_user }}"
    group: "{{ nginx_user }}"
  tags: [nginx, config]

- name: Deploy index page
  template:
    src: index.html.j2
    dest: "{{ nginx_root }}/index.html"
  tags: [nginx, config]

- name: Start Nginx
  systemd:
    name: nginx
    state: started
    enabled: yes
  tags: [nginx, service]

- name: Allow HTTP
  ufw:
    rule: allow
    port: "{{ nginx_port }}"
    proto: tcp
  when: ansible_os_family == "Debian"
  tags: [nginx, firewall]

- name: Allow HTTP (firewalld)
  firewalld:
    port: "{{ nginx_port }}/tcp"
    permanent: yes
    state: enabled
    immediate: yes
  when: ansible_os_family == "RedHat"
  tags: [nginx, firewall]
```

**`roles/nginx/templates/nginx.conf.j2`：**

```nginx
user {{ nginx_user }};
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;

    server {
        listen {{ nginx_port }};
        server_name {{ nginx_server_name }};
        root {{ nginx_root }};
        index index.html;

        location / {
            try_files $uri $uri/ =404;
        }
    }
}
```

**`roles/nginx/templates/index.html.j2`：**

```html
<!DOCTYPE html>
<html>
<head><title>{{ nginx_server_name }}</title></head>
<body>
    <h1>Welcome to {{ nginx_server_name }}</h1>
    <p>Deployed by Ansible at {{ ansible_date_time.iso8601 }}</p>
    <p>Host: {{ inventory_hostname }}</p>
</body>
</html>
```

**`roles/nginx/handlers/main.yml`：**

```yaml
---
- name: Reload Nginx
  systemd:
    name: nginx
    state: reloaded
```

### 使用 Role

```yaml
# site.yml
---
- name: Provision Web Servers
  hosts: webservers
  become: yes
  roles:
    - role: nginx
      vars:
        nginx_port: 8080
        nginx_server_name: "{{ inventory_hostname }}.example.com"
```

```bash
ansible-playbook -i inventory.ini site.yml
```

### Ansible Galaxy

从社区获取 Roles：

```bash
# 搜索
ansible-galaxy search nginx --sort downloads

# 安装
ansible-galaxy install geerlingguy.nginx

# 在 requirements.yml 中声明依赖
cat > requirements.yml << 'EOF'
roles:
  - name: geerlingguy.docker
    version: 7.1.0
  - name: geerlingguy.nginx
    version: 3.3.0
EOF

ansible-galaxy install -r requirements.yml
```

---

## 60.7 Ansible Vault

加密敏感数据（密码、密钥、证书）：

```bash
# 创建加密文件
ansible-vault create group_vars/production/vault.yml

# 编辑已有加密文件
ansible-vault edit group_vars/production/vault.yml

# 加密已有文件
ansible-vault encrypt group_vars/production/secrets.yml

# 解密
ansible-vault decrypt group_vars/production/secrets.yml

# 查看（不解密）
ansible-vault view group_vars/production/vault.yml
```

```yaml
# 加密内容示例
# group_vars/production/vault.yml
vault_db_password: "S3cretP@ss!"
vault_api_key: "sk-abc123xyz"
vault_ssl_key: |
  -----BEGIN PRIVATE KEY-----
  ...
  -----END PRIVATE KEY-----
```

### 运行时提供密码

```bash
# 交互式输入
ansible-playbook site.yml --ask-vault-pass

# 从文件读取
echo "my-vault-password" > .vault_pass
ansible-playbook site.yml --vault-password-file .vault_pass

# 环境变量
export ANSIBLE_VAULT_PASSWORD_FILE=.vault_pass
ansible-playbook site.yml
```

---

## 60.8 模块速查

| 模块 | 用途 | 示例 |
|------|------|------|
| `apt` | Debian 包管理 | `apt: name=nginx state=present` |
| `dnf` / `yum` | RHEL 包管理 | `dnf: name=httpd state=present` |
| `pacman` | Arch 包管理 | `pacman: name=nginx state=present` |
| `copy` | 复制文件 | `copy: src=file dest=/opt/file` |
| `template` | Jinja2 模板 | `template: src=conf.j2 dest=/etc/conf` |
| `file` | 文件/目录属性 | `file: path=/opt state=directory mode=0755` |
| `systemd` | 管理 systemd 服务 | `systemd: name=nginx state=started` |
| `service` | 通用服务管理 | `service: name=nginx state=restarted` |
| `user` | 用户管理 | `user: name=alice groups=sudo` |
| `group` | 组管理 | `group: name=developers state=present` |
| `git` | 克隆 Git 仓库 | `git: repo=url dest=/opt/app` |
| `lineinfile` | 按行管理文件 | `lineinfile: path=/etc/hosts line='...'` |
| `blockinfile` | 块内容管理 | `blockinfile: path=/etc/conf block='...'` |
| `command` | 执行命令 | `command: date` |
| `shell` | Shell 命令 | `shell: grep foo /etc/passwd` |
| `cron` | 管理 cron 任务 | `cron: name="backup" hour=2 job="/script"` |
| `unarchive` | 解压归档文件 | `unarchive: src=file.tar.gz dest=/opt/` |
| `uri` | HTTP 请求 | `uri: url=http://api/health status_code=200` |

---

## 60.9 完整实战：批量初始化 Web 服务器

### 项目结构

```
ansible-web/
├── ansible.cfg
├── inventory/
│   ├── staging.yml
│   └── production.yml
├── group_vars/
│   ├── all.yml
│   ├── webservers.yml
│   └── production/
│       └── vault.yml
├── site.yml
└── roles/
    ├── baseline/
    │   └── tasks/main.yml
    └── nginx/
        ├── tasks/main.yml
        ├── handlers/main.yml
        ├── templates/
        │   └── nginx.conf.j2
        └── defaults/main.yml
```

### ansible.cfg

```ini
[defaults]
inventory = inventory/staging.yml
host_key_checking = False
retry_files_enabled = False
stdout_callback = yaml
gathering = smart
```

### site.yml

```yaml
---
- name: Provision All Servers
  hosts: all
  become: yes
  roles:
    - baseline

- name: Configure Web Servers
  hosts: webservers
  become: yes
  roles:
    - nginx
```

### inventory/staging.yml

```yaml
all:
  children:
    webservers:
      hosts:
        web-stg-01:
          ansible_host: 10.0.0.10
        web-stg-02:
          ansible_host: 10.0.0.11
    databases:
      hosts:
        db-stg-01:
          ansible_host: 10.0.0.20
  vars:
    ansible_user: deploy
    ansible_ssh_private_key_file: ~/.ssh/staging_key
```

### group_vars/all.yml

```yaml
timezone: Asia/Shanghai
admin_user: opsadmin
default_packages:
  - htop
  - vim
  - git
  - curl
  - tmux
```

### 执行部署

```bash
# 预演
ansible-playbook site.yml --check --diff

# 部署
ansible-playbook site.yml

# 仅更新 Nginx 配置
ansible-playbook site.yml --tags config

# 部署到生产环境
ansible-playbook -i inventory/production.yml site.yml --ask-vault-pass

# 逐步执行（交互确认）
ansible-playbook site.yml --step
```

---

## 60.10 最佳实践

```yaml
# 1. 使用 apply 代替 --tags 执行特定 role
ansible-playbook site.yml --tags nginx    # 临时使用

# 2. 任务命名清晰，描述做了什么
- name: Install Nginx package
  apt: name=nginx

# 3. always 使用 tags（至少一个 role 级 tag）
tasks:
  - name: Install Nginx
    apt: name=nginx
    tags: [nginx, install]

# 4. handlers 命名使用动词开头
handlers:
  - name: Restart Nginx   # ✓
    ...
  - name: Nginx restart    # ✗

# 5. 敏感信息使用 Vault
ansible-vault encrypt group_vars/production/secrets.yml

# 6. 使用 ansible-lint 检查 Playbook
pip install ansible-lint
ansible-lint site.yml
```

---

## 60.11 本章总结

| 概念 | 说明 |
|------|------|
| Inventory | 主机清单，定义管理哪些服务器 |
| Module | 原子操作单元（apt、copy、systemd 等） |
| Task | 对主机执行的单一操作 |
| Playbook | 多个 Play 组成的 YAML 文件 |
| Play | 一组 Task + 目标主机 + 变量 |
| Role | 可复用的 Playbook 组织单元 |
| Handler | 被通知时才执行的任务 |
| Jinja2 | 模板引擎（`{{ variable }}`、`{% if %}`） |
| Vault | 加密敏感变量 |
| Galaxy | 社区 Role 仓库 |

> 服务器初始化基线配置见 [[54-服务器初始化与基线配置]]，CI/CD 自动化见 [[59-CI-CD基础]]。
