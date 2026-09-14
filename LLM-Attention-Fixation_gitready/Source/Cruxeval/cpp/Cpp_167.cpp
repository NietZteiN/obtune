#include<assert.h>
#include<bits/stdc++.h>

std::string f(std::string XAAXX, std::string s) {
    int count = 0;
    size_t idx = -1;
    while ((idx = XAAXX.find("XXXX", idx+1)) != std::string::npos) {
        count++;
    }
    std::string compound = s;
    std::transform(compound.begin(), compound.end(), compound.begin(), ::tolower);
    compound[0] = toupper(compound[0]);
    for (int i = 1; i < count; ++i) {
        compound += s;
        std::transform(compound.end() - s.size(), compound.end(), compound.end() - s.size(), ::tolower);
        compound[compound.size() - s.size()] = toupper(compound[compound.size() - s.size()]);
    }
    size_t start_pos = XAAXX.find("XXXX");
    while(start_pos != std::string::npos) {
        XAAXX.replace(start_pos, 4, compound);
        start_pos = XAAXX.find("XXXX", start_pos + compound.size());
    }
    return XAAXX;
}
int main() {
    auto candidate = f;
    assert(candidate(("aaXXXXbbXXXXccXXXXde"), ("QW")) == ("aaQwQwQwbbQwQwQwccQwQwQwde"));
}
