#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, long m, long n) {
    text = text + text.substr(0, m) + text.substr(n);
    std::string result = "";
    for (long i = n; i < text.length() - m; i++) {
        result = text[i] + result;
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("abcdefgabc"), (1), (2)) == ("bagfedcacbagfedc"));
}
