#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string string) {
    std::vector<char> l(string.begin(), string.end());
    for (int i = l.size() - 1; i >= 0; i--) {
        if (l[i] != ' ') {
            break;
        }
        l.pop_back();
    }
    return std::string(l.begin(), l.end());
}
int main() {
    auto candidate = f;
    assert(candidate(("    jcmfxv     ")) == ("    jcmfxv"));
}
