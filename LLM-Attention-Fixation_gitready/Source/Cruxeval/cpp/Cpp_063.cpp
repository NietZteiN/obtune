#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string prefix) {
    while(text.find(prefix) == 0) {
        text = text.substr(prefix.length());
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("ndbtdabdahesyehu"), ("n")) == ("dbtdabdahesyehu"));
}
