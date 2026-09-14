#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::string result = "";
    for (int i = 0; i < text.length(); i++) {
        if (i % 2 == 0) {
            result += std::toupper(text[i]);
        } else {
            result += text[i];
        }
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("vsnlygltaw")) == ("VsNlYgLtAw"));
}
