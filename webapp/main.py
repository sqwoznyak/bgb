import os
import uvicorn
import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Запуск FastAPI-сервера. "
                    "Используйте флаг --https-disable для отключения HTTPS-редиректа во время локальной отладки."
    )
    parser.add_argument(
        "--https-disable",
        action="store_true",
        help="Отключить middleware, перенаправляющее HTTP на HTTPS (полезно при локальном debug)"
    )
    return parser.parse_args()


def run() -> None:
    args = parse_args()

    if args.https_disable:
        os.environ["HTTPS_DISABLED"] = "true"

    uvicorn.run(
        "app:create_app", 
        factory=True,
        host="0.0.0.0",
        port=8002,
        reload=True
    )


if __name__ == "__main__":
    run()
