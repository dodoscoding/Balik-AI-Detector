# M1 prova ve nihai test ödevleri

Koordinatör kayıtları ilk karşılaştırmadan önce tamamlar. Prova dört ayrı yazardan birer İngilizce akademik ödev bölümü içerir. Nihai test için bu dört kişiden farklı 3–4 yazardan birer izinli İngilizce akademik ödev bölümü ayrılır. Bu ikinci grup nihai test kümesinin başlangıcıdır.

## Yazardan alınacak bilgiler

Aşağıdaki formu her yazara özel olarak gönder. İzinleri yazılı kaydet ve özgün yanıtı yetkili kişilerin erişebildiği, depo dışındaki alanda sakla.

> Kendi İngilizce akademik ödevinizden bir bölüm, ödev yönergesi, tek cümlelik yazım amacınız ve istediğiniz tonu paylaşır mısınız?
>
> Yazım amacınızı zaten karşılayan bir pasaj varsa, bölümdeki cümleyi aynen kopyalayıp ayrı bir alanda belirtin. Aynı cümle birden fazla yerde geçiyorsa yerini de tarif edin. Bu bilgi korunma değerlendirmesinde kullanılacak.
>
> Özgün bölümünüzün ve iki düzenlemesinin kör karşılaştırmayı yapacak akranlarla paylaşılmasına izin veriyor musunuz? **Evet / Hayır**

Bulut hizmeti düşünülüyorsa ayrı bir soru sor. Sağlayıcının adını, hangi verilerin gönderileceğini, işlemin amacını ve geçerli saklama koşullarını önce yazara bildir. Sağlayıcıya özel evet veya hayır yanıtını ve tarihi kaydet. Yeni bir sağlayıcı için ayrı izin al. Akran izni olmadan ödevi gruba alma. Bulut izni yoksa ödevi yalnızca izin kapsamındaki yerel işlemde kullan.

## Kayıt ve erişim

1. Depo dışında, erişimi sınırlı bir yerde her gerçek yazara tek bir rastgele kod ver. Aynı kişiyi iki kez saymamak için izin kayıtlarını kontrol et. Kimlik eşlemesini ve izin kanıtını kodlu listeden ayrı tut.
2. Her kaynak ödeve tek bir kod ver. Alıntılanan bölümlere ve yapay zekâ, karma veya düzenlenmiş sürümlere ayrı kodlar verip kaynak ödevin altında kaydet. Aynı kaynak veya bölüm yeniden ortaya çıkarsa özgün kodunu kullan. Koordinatör bir alıntının veya türevin başka bir gruba ait olup olmadığını kontrol eder.
3. Yazarın işaretlediği pasajı ve konumunu karşılaştırmadan önce ayrı bir özel kayda yaz. İşaret yoksa bunu da kaydet. İki editör girdisini aynı dört alandan hazırla: tam ödev bölümü, yönerge, tek cümlelik amaç ve ton. Pasaj özgün bölümün içinde yerinde kalır. İşaret, konum ve koordinatör notları editör girdisinin dışında tutulur.
4. Prova malzemesi ile nihai malzemeyi ayrı erişim alanlarında sakla. Nihai içerik yalnızca saklama ve izin işlemlerini yürüten yetkililere açık kalır. Talimatlar sabitlendikten sonra nihai malzemeyi yalnızca nihai testi yürüten yetkili ekip kullanır. İlk karşılaştırmadan önce kodlu kayıtları tarihle ve ayrımı doğrula. Yeni türevleri oluşturuldukça kaynaklarının altında kaydet ve kontrolü yeniden çalıştır.

## Kodlu doğrulama

Depo dışındaki UTF-8 JSON dosyasında `rehearsal` ve `final` dizileri kullan. Her satır bir yazara ait bir kaynak ödevdir. Aşağıdaki satır alan biçimini gösterir. Kodlar büyük harfle başlar ve büyük ASCII harf, rakam, alt çizgi veya kısa çizgiden oluşur.

```json
{
  "author": "W-8F3A",
  "draft": "D-71B2",
  "related": ["P-4C13"],
  "peer_permission": true,
  "cloud_permission": "not_requested"
}
```

`related` kaynağa bağlı pasaj ve türev kodlarını içerir. Henüz ek kayıt yoksa boş liste kullan. `peer_permission` yazılı onaya dayanır. `cloud_permission` için `not_requested`, `declined` veya `granted` kullan. Sağlayıcı adı ve izin belgesi özel kayıtta kalır.

```sh
python3 scripts/check_m1_split.py /özel/dizin/kodlu-kayit.json
```

Kontrolü yapan kişi iki gruptaki yazar ve kaynak taslak sayılarını, kod tekrarlarını ve izin durumunu doğrular. Kod denetimi, aynı kişiye veya içeriğe farklı kod verilmesini tespit edemediği için koordinatör izin ve kaynak eşlemelerini özel kayıttan ayrıca doğrular. Prova türevleri yeni kaynak ödev veya yazar olarak sayılmaz.

GitHub'a yalnızca şu biçimde anonim toplu sonuç girilir. Gerçek kayıtlar tamamlanana kadar durumu **bekliyor** olarak tut.

| Prova yazar / kaynak ödev | Nihai test yazar / kaynak ödev | Ayrım kontrolü |
| --- | --- | --- |
| … / … | … / … | Bekliyor / Geçti / Başarısız |

## Birincil kaynak adayları

Katılımcıların sağladığı gerçek ders planlarını ve proje bölümlerini depo dışındaki özel kaynak envanterinde kaydet. Dosya sayısı, yazar ve ödev sayısından ayrı tutulur. Bir dosya birden çok ders planı içerebilir. Ortak proje metninde ilgili bölümün yazarlığını ve bağlı bölümleri doğrula. Ortak içeriği, aynı projeye bağlı bölümleri ve ortak yazarları iki gruba dağıtma.

Adayı kodlu ayrım kaydına almadan önce yazar, özgün ödev ve izin bilgilerini doğrula. Ders planındaki öğrenci etkinliği talimatlarını ve pedagojik hedefleri, yazarın ödevi hazırlarken aldığı yönerge ve belirttiği yazım amacı için bağlam olarak kullan. Asıl yönergeyi ve yazım amacını yazardan al.

## İnsan yazımı referansları

Kullanıcının sağladığı üç yayımlanmış metin İngilizce teknik yazım için referanstır.

| Metin | İncelenecek yazım özelliği |
| --- | --- |
| Edsger W. Dijkstra, *Go To Statement Considered Harmful* | Bir savı doğrudan kurma ve gerekçelendirme |
| Jeffrey Dean ve Sanjay Ghemawat, *MapReduce: Simplified Data Processing on Large Clusters* | Teknik bir modeli tanımlama ve uygulama ayrıntılarını açıklama |
| Ashish Vaswani ve diğerleri, *Attention Is All You Need*, arXiv v1 | Yöntem, karşılaştırma ve nicel bulguları sunma |

Bu kaynaklar prova veya nihai test ödev sayısına dahil edilmez. Bir katılımcı ödevinde bu kaynaklardan alıntı varsa o alıntıyı ödevle birlikte kodla. Yayımlanmış referansların kendisi için ayrı bir katılımcı kaydı açma.
