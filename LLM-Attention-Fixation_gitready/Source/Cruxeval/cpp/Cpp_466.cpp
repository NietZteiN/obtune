#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    size_t length = text.length();
    size_t index = 0;
    while (index < length && isspace(text[index])) {
        index++;
    }
    return text.substr(index, 5);
}
int main() {
    auto candidate = f;
    assert(candidate(("-----	\n	th\n-----")) == ("-----"));
}
