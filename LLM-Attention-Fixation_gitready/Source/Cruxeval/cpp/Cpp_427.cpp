#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s) {
    int count = s.length() - 1;
    std::string reverse_s = s;
    std::reverse(reverse_s.begin(), reverse_s.end());
    while (count > 0 && reverse_s.substr(0, count).find("sea") == std::string::npos) {
        count--;
        reverse_s = reverse_s.substr(0, count);
    }
    return reverse_s.substr(count);
}
int main() {
    auto candidate = f;
    assert(candidate(("s a a b s d s a a s a a")) == (""));
}
