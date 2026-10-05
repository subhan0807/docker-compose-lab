from flask import Flask, jsonify
import os
import socket
import psycopg2
import redis

app = Flask(__name__)

PORT = 8080


def get_database_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT", 5432),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD")
    )


def get_redis_connection():
    return redis.Redis(
        host=os.environ.get("REDIS_HOST"),
        port=int(os.environ.get("REDIS_PORT", 6379)),
        decode_responses=True
    )


@app.route("/")
def home():

    database_status = "unknown"
    redis_status = "unknown"

    # Test PostgreSQL
    try:
        connection = get_database_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT NOW()")
        cursor.fetchone()

        cursor.close()
        connection.close()

        database_status = "connected"

    except Exception as error:
        print("PostgreSQL error:", error)
        database_status = "failed"

    # Test Redis
    try:
        redis_client = get_redis_connection()
        redis_client.ping()

        redis_status = "connected"

    except Exception as error:
        print("Redis error:", error)
        redis_status = "failed"

    return jsonify({
        "application": "Docker Compose Python Demo",
        "backend": "Python Flask",
        "database": database_status,
        "redis": redis_status,
        "hostname": socket.gethostname()
    })


@app.route("/health")
def health():

    return jsonify({
        "status": "healthy"
    }), 200


@app.route("/database")
def database_test():

    try:

        connection = get_database_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT NOW()")
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        return jsonify({
            "database": "PostgreSQL",
            "status": "connected",
            "server_time": str(result[0])
        })

    except Exception as error:

        return jsonify({
            "database": "PostgreSQL",
            "status": "failed",
            "error": str(error)
        }), 500


@app.route("/redis")
def redis_test():

    try:

        redis_client = get_redis_connection()

        redis_client.set("docker_course", "Docker Compose with Python")

        value = redis_client.get("docker_course")

        return jsonify({
            "redis": "connected",
            "value": value
        })

    except Exception as error:

        return jsonify({
            "redis": "failed",
            "error": str(error)
        }), 500


if __name__ == "__main__":

    print("Starting Python Flask backend...")

    app.run(
        host="0.0.0.0",
        port=PORT
    )
