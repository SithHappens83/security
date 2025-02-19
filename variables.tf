#variable "cloudflare_email" {
#description = "Cloudflare account email"
#type        = string
#} 

/* variable "cloudflare_api_key" {
  description = "Cloudflare API key"
  type        = string
} */

/* ariable "cloudflare_zone_id" {
  description = "Cloudflare Zone ID for the domain"
  type        = string
} */

variable "domain_name" {
  description = "The domain name for the API"
  default     = "secure-file-upload.nateembree.com"
  type        = string
}
