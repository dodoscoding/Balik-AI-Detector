# Sıfır bütçeyle dört taslağı karşılaştırma

Kaynak kontrolü 21 Kasım 2026 tarihinde yapıldı.

## Yerel seçenek

`llama.cpp` ile Qwen3-4B-Instruct-2507 modelinin GGUF dosyası mevcut ve uygun bir bilgisayarda çalışabilir. Qwen modelini Apache 2.0 lisansıyla yayımlıyor. GGML ekibinin Q8_0 dosyası 4,28 GB disk alanı kaplıyor. Bu boyut RAM gereksinimini göstermez. Uygunluk; donanıma, kullanılabilir belleğe ve taslakla birlikte modele verilen toplam metin uzunluğuna bağlıdır. Mevcut donanım uygunsa model için API ücreti çıkmaz. Model dosyası alındıktan sonra yerel çalıştırmada katılımcı metinlerini bir sağlayıcıya göndermek gerekmez. [Qwen model kartı](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507) · [GGML model dosyası](https://huggingface.co/ggml-org/Qwen3-4B-Instruct-2507-Q8_0-GGUF/tree/main) · [Qwen yerel çalışma belgeleri](https://github.com/QwenLM/Qwen3/blob/main/docs/source/run_locally/llama.cpp.md)

Karşılaştırmaya başlarken model dosyasının adını ve SHA-256 özetini, `llama.cpp` sürümünü, sohbet şablonunu, bağlam ve çıktı sınırlarını, sıcaklığı ve rastgelelik tohumunu kaydet. İki düzenlemede aynı ayarları ve ayrı oturumları kullan. [llama.cpp komut satırı belgeleri](https://github.com/ggml-org/llama.cpp/blob/master/tools/cli/README.md)

## Barındırılan seçenek

Google, Gemini 3.5 Flash-Lite için standart ücretsiz katmanda girdi ve çıktı ücretini sıfır olarak listeliyor. API erişimi etkin bir proje ve anahtar gerektirir. Bazı projelerde doğrulama istenebilir. Sekiz düzenleme isteği için kota ve model erişimi proje üzerinden kontrol edilmeli. Sabit model kimliğini ve üretim ayarlarını kaydet. API kullanılırsa her yanıtın `modelVersion` alanını da kaydet. [Fiyatlandırma](https://aistudio.google.com/docs/pricing#gemini-3.5-flash-lite) · [Model sürümü](https://aistudio.google.com/docs/models/gemini-3.5-flash-lite) · [API anahtarı](https://aistudio.google.com/docs/api-key) · [Kotalar](https://aistudio.google.com/docs/rate-limits) · [Yanıt alanları](https://aistudio.google.com/api-reference/generate-content)

Girdi ve çıktı Google tarafından işlenir. Google’ın genel ücretsiz kullanım koşulları, içerik ve yanıtların ürün geliştirme için kullanılabileceğini ve insanlar tarafından incelenebileceğini belirtiyor. Avrupa Ekonomik Alanı, İsviçre ve Birleşik Krallık için ücretsiz kullanımda da ücretli hizmetlerin veri hükümleri uygulanıyor. Bu hükümlerde ürün geliştirme için kullanım yapılmadığı ve güvenlik gibi belirtilen amaçlarla verilerin sınırlı süre tutulabileceği yazıyor. Aynı koşullar bu bölgelerde son kullanıcılara sunulan API istemcileri için ücretli hizmet şartı koyuyor. Bu seçenek, ileride kullanıcılara sunulacak bir entegrasyona dair karar olmadan, değerlendirmeyi yürüten kişinin erişimi ve katılımcıların açıkça izin verdiği içerik için ele alınabilir. [Google Gemini API koşulları](https://aistudio.google.com/docs/terms) · [Desteklenen bölgeler](https://aistudio.google.com/docs/available-regions)

## İlk deneme için öneri

Katılımcıların kendi metinleri için önce mevcut bilgisayarda yerel seçeneğin uygunluğunu değerlendir. Donanım yetersizse bulutta önce kişisel bilgi içermeyen sentetik bir örnekle kör değerlendirme akışını prova etmek, katılımcı metinlerini paylaşmadan ilerlemeyi sağlar. Katılımcı taslakları bulutta işlenecekse metinlerin Google’a gideceğini paylaşım iznine dahil et ve proje kotasını doğrula.

Her taslak için iki düzenleyiciye aynı özgün metni, bir cümlelik yazım amacını ve ton isteğini ver. Ortak model ve ayarlarla iki sürümü ayrı oturumlarda üret. Her iki talimatın tam metnini, üretim tarihini ve ham çıktıları kaydet. A/B kimliklerini ve varsa tarama puanlarını değerlendirme materyalinden çıkar. [Balik yol haritası](../../ROADMAP.md#blind-comparison-and-beta-criteria)

Bu araştırma belgelere dayanır. Model performansı, cihaz uygunluğu ve proje erişimi henüz ölçülmedi.
