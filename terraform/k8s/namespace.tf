resource "kubernetes_namespace" "dev_env" {
  metadata {
    name = "dev-env"
  }
}