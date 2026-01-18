FROM golang:alpine AS builder

WORKDIR /app

RUN apk add -U --no-cache git

RUN git clone https://github.com/WiiLink24/NintendoChannel .
RUN go build -o app cli/main.go

FROM python:3.10-alpine

RUN adduser -D server
WORKDIR /home/server

# Copy requirements first as to not disturb cache for other changes.
COPY requirements.txt .

# Install dependencies
RUN apk add -U --no-cache libpq-dev build-base

RUN pip3 install -r requirements.txt && \
  pip3 install gunicorn

USER server

# Finally, copy the entire source.
COPY . .

# Copy file generator
COPY --from=builder /app/app cli

ENV FLASK_APP app.py
EXPOSE 5000
ENTRYPOINT ["gunicorn", "-b", ":5000", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
