# CV Sync Service - GDPR Quick Guide

**Quick reference for GDPR compliance when using the CV sync service**

---

## ⚖️ Legal Basis: Legitimate Interest

**GDPR Article 6(1)(f)**: Processing CVs uploaded via sync service is based on the recruitment agency's legitimate interest in efficiently processing candidate applications.

---

## ✅ Your GDPR Compliance Checklist

### Before Starting

- [ ] Update your privacy policy to mention automated CV processing
- [ ] Add processing notice to your website and email signatures
- [ ] Set data retention period in Tanova (Settings → GDPR)
- [ ] Document your legitimate interest assessment (see template below)
- [ ] Ensure only authorized staff have Tanova access
- [ ] Store API keys securely (not in code repositories)

### Ongoing Compliance

- [ ] **Monthly**: Review candidates approaching retention limit
- [ ] **Monthly**: Process any deletion requests within 30 days
- [ ] **Quarterly**: Audit team access and API key usage
- [ ] **Annually**: Update privacy policy and staff training

---

## 📝 Required Privacy Notice

Add this to your website, emails, and job postings:

```
DATA PROCESSING NOTICE

CVs submitted to [Your Company] may be processed using automated
recruitment software (Tanova) to match candidates with suitable
positions. We process your data under our legitimate business
interest in recruitment.

Your rights:
• Access your data
• Request corrections
• Request deletion
• Object to processing

Data retention: We keep CVs for [X] years, then automatically delete them.

For more information, see our privacy policy: [link]
```

---

## 🔍 Legitimate Interest Assessment (Template)

Document and keep on file:

### 1. Purpose Test
**What are you trying to achieve?**
> Efficiently process candidate CVs for recruitment purposes using automated matching

### 2. Necessity Test
**Is this processing necessary?**
> Yes - Manual CV processing would significantly delay candidate responses and reduce recruitment efficiency

### 3. Balancing Test
**Do candidate interests override your interests?**
> No - Candidates voluntarily send CVs expecting them to be processed for job opportunities. The processing is limited to recruitment purposes with strong security measures.

**Risk mitigation:**
- Data encrypted in transit and at rest
- Automatic deletion after retention period
- Candidates can request deletion at any time
- Access restricted to authorized staff only

**Conclusion:**
> Legitimate interest applies. The business need for efficient recruitment outweighs the minimal privacy impact, as candidates expect and consent to CV processing when applying for jobs.

---

## 🛡️ What Tanova Handles for You

✅ **Automatic retention enforcement** - CVs auto-delete after your set period
✅ **Secure storage** - S3 encryption, HTTPS, access controls
✅ **Audit logs** - All data access logged
✅ **Data export** - For subject access requests
✅ **Safe deletion** - Removes CV + database record + anonymizes analytics
✅ **API security** - Key-based authentication with usage tracking

---

## ⚠️ What You Must Handle

❌ **Informing candidates** - Add processing notice to your communications
❌ **Privacy policy** - Maintain up-to-date policy
❌ **Deletion requests** - Respond within 30 days
❌ **Access requests** - Provide data copy within 30 days (use Tanova export)
❌ **Staff training** - Ensure team understands GDPR obligations
❌ **Legal basis documentation** - Keep your LIA on file

---

## 📊 Data Subject Rights & How to Handle

| Right | What it means | How to handle in Tanova |
|-------|---------------|------------------------|
| **Access** | Candidate wants a copy of their data | Settings → GDPR → Export specific candidate data |
| **Rectification** | Candidate wants to correct info | Edit candidate record in Tanova |
| **Erasure** | Candidate wants deletion | Delete candidate (removes CV from S3 too) |
| **Restriction** | Candidate objects to processing | Archive candidate and stop processing |
| **Portability** | Candidate wants data in machine format | Use GDPR export feature (JSON format) |
| **Object** | Candidate objects to legitimate interest | Must stop processing unless compelling grounds |

**Response time**: 30 days (can extend 60 days if complex)

---

## 🚨 Data Breach Response Plan

If CVs are accidentally exposed or leaked:

### Immediate Actions (Day 1)
1. **Contain**: Stop the breach source (revoke API key, fix vulnerability)
2. **Assess**: How many affected? What data exposed?
3. **Document**: Record what happened, when, how

### Report if High Risk (Within 72 hours)
Report to your Data Protection Authority (DPA) if:
- Sensitive data exposed (health, ethnicity, etc.)
- Large number of candidates affected (>100)
- Could cause significant harm to individuals

### Notify Candidates if High Risk
Inform affected candidates directly if:
- High risk to their rights/freedoms
- Could lead to identity theft, discrimination, etc.

### Example: Lost USB with CVs
- **Risk**: High (physical data loss, no encryption)
- **Action**: Report to DPA + notify candidates + document

### Example: Exposed API key (quickly revoked)
- **Risk**: Low (no actual access occurred, key revoked)
- **Action**: Document internally, no external reporting needed

---

## 🌍 Cross-Border Considerations

### EU/EEA Agencies
✅ No issues - data stays in EU

### UK Agencies
✅ No issues - UK GDPR equivalent applies

### Non-EU Agencies Processing EU Data
⚠️ **GDPR Still Applies** if:
- You offer services to EU residents
- You monitor behavior of EU residents

**Requirements:**
- Appoint EU representative (if >250 employees)
- Comply with GDPR as if EU-based
- Use Standard Contractual Clauses for data transfers

---

## 📞 When to Get Legal Help

Consult a data protection lawyer if:
- 🔴 You process **sensitive categories** (health, ethnicity, criminal records)
- 🔴 You're a **large organization** (>250 employees)
- 🔴 You make **solely automated decisions** that significantly affect candidates
- 🔴 You process data about **children** (<16 years old)
- 🔴 You've had a **data breach** with potential harm
- 🔴 You're **transferring data internationally** outside EU/EEA
- 🔴 A candidate has **objected** to processing

---

## 🔗 Quick Reference Links

- **Full CV Sync Documentation**: [Complete implementation details and GDPR compliance](/docs/CV_SYNC_SERVICE.md)
- **Tanova GDPR Settings**: Settings → GDPR & Compliance
- **ICO Guidance (UK)**: https://ico.org.uk
- **GDPR Text**: https://gdpr-info.eu
- **Your DPA**: Search "[your country] data protection authority"

---

## ✉️ Example Email Signature

```
[Your Name]
[Your Company] - Recruitment Specialist
Email: [email] | Phone: [phone]

Privacy Notice: We use automated software to process CVs.
Your data rights: tanova.ai/privacy
```

---

## 📋 Quick Compliance Test

Answer these questions:

1. ☑️ Can candidates see your privacy policy from your website?
2. ☑️ Does it mention automated CV processing?
3. ☑️ Have you set a data retention period (≤2 years recommended)?
4. ☑️ Do you know how to export a candidate's data?
5. ☑️ Do you know how to delete a candidate?
6. ☑️ Have you documented why legitimate interest applies?
7. ☑️ Are your API keys stored securely?
8. ☑️ Do only authorized staff have Tanova access?

**8/8**: ✅ You're GDPR compliant!
**5-7/8**: ⚠️ Almost there - fix the gaps
**<5/8**: 🔴 Compliance risk - address urgently

---

## 💡 Remember

**GDPR is not scary** - it's about:
1. Being transparent with candidates
2. Keeping data secure
3. Not keeping data forever
4. Respecting candidate rights

✅ Use Tanova's built-in features
✅ Follow this checklist
✅ Update your privacy policy
✅ Train your team

You'll be compliant! 🎉

---

**Questions?** support@tanova.ai | In-app chat

**Last Updated**: December 2025
