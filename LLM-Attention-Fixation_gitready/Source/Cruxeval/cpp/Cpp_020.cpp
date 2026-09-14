#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::string result = "";
    for (int i = text.length() - 1; i >= 0; i--) {
        result += text[i];
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("was,")) == (",saw"));
}
