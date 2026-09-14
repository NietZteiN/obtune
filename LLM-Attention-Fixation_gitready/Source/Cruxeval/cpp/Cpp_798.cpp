#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string pre) {
    if (text.substr(0, pre.length()) != pre) {
        return text;
    }
    return text.substr(pre.length());
}
int main() {
    auto candidate = f;
    assert(candidate(("@hihu@!"), ("@hihu")) == ("@!"));
}
