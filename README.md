# API Calculator — DevSecOps

Учебный REST API на Python 3.13 и FastAPI. Docker обеспечивает изолированный запуск, GitHub Actions автоматически тестирует, собирает и проверяет проект при каждом push. Используются Semgrep (SAST) и Trivy (анализ известных уязвимостей компонентов Docker-образа).

## 1. Структура проекта

- `main.py` — API и проверка аргументов.
- `requirements.txt` — зависимости приложения.
- `requirements-dev.txt` — зависимости для тестов.
- `Dockerfile`, `.dockerignore` — сборка контейнера.
- `tests/test_api.py` — автоматические тесты.
- `.github/workflows/ci.yml` — пайплайн GitHub Actions.
- `.github/dependabot.yml` — предложения обновлений зависимостей.
- `SECURITY_ANALYSIS.md` — исходные результаты сканирования, исправления и порядок повторной проверки.

## 2. Методы API

Все вычислительные методы используют HTTP GET с параметрами `a` и `b` (конечные вещественные числа). Результат возвращается в JSON.

| Метод | Операция | Пример | Результат |
|---|---|---|---|
| `/add` | Сложение | `?a=2&b=3` | 5 |
| `/subtract` | Вычитание | `?a=7&b=2` | 5 |
| `/multiply` | Умножение | `?a=2&b=3` | 6 |
| `/divide` | Деление | `?a=7&b=2` | 3.5 |
| `/power` | Степень | `?a=2&b=3` | 8 |
| `/mod` | Остаток от деления | `?a=7&b=3` | 1 |
| `/version` | Версия | без параметров | `{"version":"local"}` по умолчанию |

`/` — проверка доступности; `/docs` — Swagger UI; `/openapi.json` — схема API.

HTTP 200 — успех; 400 — недопустимая операция или неконечный результат; 422 — отсутствующий/некорректный параметр (включая NaN и Infinity). Используется float, поэтому возможны обычные погрешности представления вещественных чисел. Это не финансовый калькулятор. Нагрузочное тестирование не проводилось.

## 3. Локальный запуск (Windows PowerShell)

Установите Python 3.13, Docker Desktop (с Linux-контейнерами) и Git. Откройте PowerShell в корне проекта.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Откройте <http://127.0.0.1:8000/docs>. Для остановки локального Uvicorn нажмите Ctrl+C перед запуском Docker на том же порту.

## 4. Docker

```powershell
docker build --pull --build-arg APP_VERSION=1.0.0 -t calculator-api:1.0.0 .
docker run -d --name calculator-container -p 127.0.0.1:8000:8000 calculator-api:1.0.0
docker ps
docker exec calculator-container id
curl.exe "http://127.0.0.1:8000/add?a=2&b=3"
curl.exe "http://127.0.0.1:8000/version"
curl.exe -i "http://127.0.0.1:8000/divide?a=5&b=0"
```

Ожидаемые ответы: `{"result":5.0}`, `{"version":"1.0.0"}`, HTTP 400 с объяснением. `id` должен показать UID 10001. Публикация порта только на loopback ограничивает доступ снаружи. Для остановки и удаления контейнера: `docker rm -f calculator-container`.

## 5. Публикация на GitHub

Создайте новый **публичный пустой** репозиторий `calculator-api` без README, лицензии и .gitignore. Не публикуйте секреты. В PowerShell из корня распакованного проекта выполните:

```powershell
git init
git add .
git commit -m "Initial calculator DevSecOps project"
git branch -M main
git remote add origin https://github.com/USERNAME/calculator-api.git
git push -u origin main
```

Замените `USERNAME` на свой логин; при необходимости настройте `git config user.name` и `git config user.email`, затем авторизуйтесь через Git Credential Manager. Если репозиторий уже существует, не выполняйте `git init` и не меняйте remote без необходимости: скопируйте файлы в существующий локальный репозиторий и выполните `git add`, `git commit`, `git push`.

Откройте вкладку **Actions**. Workflow `Calculator CI Security` запускается при push в любую ветку и вручную (`Run workflow`). Две задачи выполняются независимо:

1. Test, build and scan image: установка зависимостей, тесты, сборка образа, запуск и проверка API, сохранение образа, Trivy и выгрузка отчёта.
2. Semgrep source scan: анализ исходного кода и конфигурации, выгрузка JSON-отчёта.

Версия `1.0.N` формируется из `github.run_number` и передаётся в Docker через `--build-arg APP_VERSION`. Повторный запуск того же workflow run сохраняет номер версии; `run_attempt` различает артефакты. Образ сохраняется как TAR-артефакт (14 дней), его можно скачать и загрузить `docker load -i calculator-api.tar`. Деплой на постоянный внешний сервер не настроен: для задания используется локальный запуск и временный контейнер CI.

Чтобы показать обновление, измените, например, сообщение в `home()` (добавьте `version` в ответ), сохраните файл, затем:

```powershell
git add main.py
git commit -m "Add version to home response"
git push
```

Сравните версии и логи двух запусков. Dependabot предлагает обновления через PR; они вступают в силу после проверки и слияния, а не автоматически меняют исходный код при каждом push.

## 6. Отчёты безопасности

В Actions откройте конкретный запуск, изучите шаги `Run Semgrep` и `Run Trivy`; внизу страницы скачайте артефакты `semgrep-N-A`, `trivy-N-A`. В JSON Semgrep смотрите `results` и `errors`, в Trivy — `Results[].Vulnerabilities`, `VulnerabilityID`, `PkgName`, `InstalledVersion`, `FixedVersion`, `Severity`.

Режим сканирования отчётный: наличие находок само по себе не блокирует сборку. Ошибка запуска инструмента — не успешная проверка. Для строгого режима добавьте `--error` для Semgrep и `--exit-code 1` для Trivy. Trivy проверяет HIGH и CRITICAL, включая уязвимости без доступного исправления. Теги образов сканеров закреплены по версии, но для строгой воспроизводимости следует закрепить их и базовый образ по digest. Результаты зависят от актуальности базы и правил.

Порядок анализа и исходные результаты: [SECURITY_ANALYSIS.md](SECURITY_ANALYSIS.md).

## 7. Источники

- [FastAPI](https://fastapi.tiangolo.com/)
- [Dockerfile reference](https://docs.docker.com/reference/dockerfile/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Semgrep CI](https://semgrep.dev/docs/semgrep-ci/sample-ci-configs)
- [Trivy image scanning](https://trivy.dev/docs/latest/target/container_image/)

## Статус проверки

25 ноября 2026 года успешно завершились автоматический [запуск №16](https://github.com/Svyatoixaxa/ApiCalculator-DevSecOps/actions/runs/45557243979) и ручной [запуск №17](https://github.com/Svyatoixaxa/ApiCalculator-DevSecOps/actions/runs/45557482878). В запуске №17 успешно пройдены 6 групп тестов, собран и запущен Docker-образ calculator-api:1.0.17, проверены версия API, результат сложения и UID 10001. Semgrep обнаружил 4 замечания (330 правил, 10 файлов); Trivy — 58 записей HIGH (53 в пакетах Debian 13.8 и 5 в Python-пакетах), 0 CRITICAL. Отчеты и образ сохранены в артефактах запуска. Сканирование работает в отчетном режиме; обнаруженные проблемы не блокируют сборку. Подробности и рекомендации: [SECURITY_ANALYSIS.md](SECURITY_ANALYSIS.md).

План демонстрации: [DEFENSE.md](DEFENSE.md). Постоянный внешний сервер не разворачивался; работоспособность контейнера подтверждена в CI.
