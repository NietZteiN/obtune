#include<assert.h>
#include<bits/stdc++.h>
long f(std::string strand, std::string zmnc) {
    size_t poz = strand.find(zmnc);
    while (poz != std::string::npos) {
        strand = strand.substr(poz + 1);
        poz = strand.find(zmnc);
    }
    return strand.rfind(zmnc);
}
int main() {
    auto candidate = f;
    assert(candidate((""), ("abc")) == (-1));
}
