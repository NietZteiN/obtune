#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, long n) {
    if (n < 0 || text.length() <= n) {
        return text;
    }
    std::string result = text.substr(0, n);
    int i = result.length() - 1;
    while (i >= 0) {
        if (result[i] != text[i]) {
            break;
        }
        i--;
    }
    return text.substr(0, i + 1);
}
int main() {
    auto candidate = f;
    assert(candidate(("bR"), (-1)) == ("bR"));
}
