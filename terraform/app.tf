resource "kubernetes_deployment" "ai_app" {
  metadata {
    name      = "ai-demo-app"
    namespace = kubernetes_namespace.dev_env.metadata[0].name
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "ai-demo-app"
      }
    }

    template {
      metadata {
        labels = {
          app = "ai-demo-app"
        }
      }

      spec {
        container {
          name  = "app"
          image = "python:3.9-slim"

          command = ["/bin/sh"]

          args = [
            "-c",
            <<-EOF
            while true; do
              echo '{"level":"INFO","message":"App running","service":"ai-demo-app"}'
              sleep 2
              echo '{"level":"ERROR","message":"Database connection failed","service":"ai-demo-app"}'
              sleep 3
              echo '{"level":"WARNING","message":"High memory usage","service":"ai-demo-app"}'
              sleep 4
            done
            EOF
          ]
        }
      }
    }
  }
}