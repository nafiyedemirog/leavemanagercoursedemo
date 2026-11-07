# Domain

> Bootstrap'ta belirlendi (2026-11-07). İş, insanlar ve ajanlar arasındaki ortak dil.
> Bir terim burada yoksa, yapay zekâ kendi anlamını uydurur — eksik terimi buraya ekleyin.

## Ubiquitous language

| Term | Meaning | Notes / not to be confused with |
|---|---|---|
| Çalışan (`Employee`, rol `EMPLOYEE`) | İzin talebi oluşturan kullanıcı | Yönetici de bir `Employee` kaydıdır; farkı rolüdür |
| Yönetici (`MANAGER`) | Talepleri onaylayan/reddeden kullanıcı | Takım hiyerarşisi yok: her yönetici her talebi görür (kendi talebi hariç onaylayamaz) |
| İzin talebi (`LeaveRequest`) | Bir çalışanın belirli tarih aralığı için izin isteği | Onaylanmış izin de bir talep kaydıdır (durumu `APPROVED`) |
| İzin türü (`LeaveType`) | `ANNUAL` (yıllık), `EXCUSE` (mazeret), `SICK` (hastalık) | Yalnızca `ANNUAL` bakiyeden düşer |
| Durum (`LeaveStatus`) | `PENDING` (beklemede), `APPROVED` (onaylı), `REJECTED` (reddedildi) | Bu sürümde iptal durumu yok |
| Bakiye (`LeaveBalance`) | Çalışanın kalan yıllık izin günü (tam sayı) | Bekleyen talepler bakiyeyi değiştirmez |
| Gün sayısı | Başlangıç ve bitiş dahil takvim günü sayısı | Hafta sonu / resmi tatil düşülmez |
| Ret gerekçesi | Yöneticinin reddederken yazdığı açıklama | Ret için zorunlu |

## Business rules
- **BR-1:** İzin türleri yalnızca `ANNUAL`, `EXCUSE`, `SICK`'tir; başka değer kabul edilmez.
- **BR-2:** Gün sayısı = bitiş − başlangıç + 1 (takvim günü; başlangıç ve bitiş dahil). Bitiş, başlangıçtan önce olamaz.
- **BR-3:** Yalnızca `ANNUAL` türündeki talepler bakiyeyi etkiler.
- **BR-4:** Bakiye, talep **onaylandığında** düşer; `PENDING` bir talep bakiyeyi değiştirmez.
- **BR-5:** Negatif bakiye yasaktır: gün sayısı mevcut bakiyeyi aşan `ANNUAL` talebi oluşturulamaz ve onaylanamaz (onay anında yeniden denetlenir).
- **BR-6:** Aynı çalışanın `PENDING` veya `APPROVED` talepleri tarih olarak çakışamaz (tek gün ortaklık da çakışmadır).
- **BR-7:** Reddedilen talep bakiyeyi etkilemez; ret gerekçesi zorunludur (boş olamaz).
- **BR-8:** Yalnızca `PENDING` bir talep onaylanabilir veya reddedilebilir; `APPROVED`/`REJECTED` talep değiştirilemez.
- **BR-9:** Onaylama ve reddetme yalnızca `MANAGER` rolüne açıktır; yönetici **kendi talebini** onaylayamaz/reddedemez.
- **BR-10:** Çalışan yalnızca kendi taleplerini ve kendi bakiyesini görür; yönetici tüm talepleri görür.

## Key domain invariants
- Bakiye hiçbir koşulda sıfırın altına inmez.
- Bir talebin bakiyeye etkisi en fazla bir kez uygulanır (yalnızca `PENDING → APPROVED` geçişinde).
- Durum geçişleri yalnızca `PENDING → APPROVED` ve `PENDING → REJECTED`'tir.
- Bakiye ve durum değişikliği aynı transaction içinde olur: biri olup diğeri olmaz durumu yoktur.

## Sensitive areas
- **İzin bakiyesi** (`LeaveBalance`, BR-3…BR-5) — hata, çalışanın hak kaybı ya da fazladan izin demektir.
- **Onay kayıtları ve durum geçişleri** (BR-7, BR-8) — kim neyi ne zaman onayladı, geri alınamaz.
- **Kimlik doğrulama ve yetkilendirme** (oturum, rol, sahiplik; BR-9, BR-10, `docs/security.md`).
