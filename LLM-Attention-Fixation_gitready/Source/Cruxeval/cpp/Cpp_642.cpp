#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    int i = 0;
    while (i < text.length() && std::isspace(text[i])) {
        i++;
    }
    if (i == text.length()) {
        return "space";
    }
    return "no";
}
int main() {
    auto candidate = f;
    assert(candidate(("     ")) == ("space"));
}
