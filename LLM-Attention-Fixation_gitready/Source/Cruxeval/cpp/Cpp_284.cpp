#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string prefix) {
    int idx = 0;
    for (char letter : prefix) {
        if (text[idx] != letter) {
            return "";
        }
        idx++;
    }
    return text.substr(idx);
}
int main() {
    auto candidate = f;
    assert(candidate(("bestest"), ("bestest")) == (""));
}
