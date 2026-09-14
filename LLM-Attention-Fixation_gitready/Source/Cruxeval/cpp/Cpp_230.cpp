#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::string result = "";
    int i = text.length() - 1;
    while (i >= 0) {
        char c = text[i];
        if (isalpha(c)) {
            result += c;
        }
        i--;
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("102x0zoq")) == ("qozx"));
}
