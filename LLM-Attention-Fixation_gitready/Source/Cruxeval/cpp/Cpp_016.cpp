#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string suffix) {
    if (text.substr(text.size() - suffix.size()) == suffix) {
        return text.substr(0, text.size() - suffix.size());
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("zejrohaj"), ("owc")) == ("zejrohaj"));
}
