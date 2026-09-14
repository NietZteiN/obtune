#include<assert.h>
#include<bits/stdc++.h>
long f(std::string text) {
    int a = text.length();
    int count = 0;
    while (!text.empty()) {
        if (text.substr(0, 1) == "a") {
            count += text.find(' ');
        } else {
            count += text.find('\n');
        }
        text = text.substr(text.find('\n')+1, a+1);
    }
    return count;
}
int main() {
    auto candidate = f;
    assert(candidate(("a\nkgf\nasd\n")) == (1));
}
