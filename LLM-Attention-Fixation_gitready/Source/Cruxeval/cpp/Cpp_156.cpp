#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, long limit, std::string char_str) {
    if (limit < text.length()) {
        return text.substr(0, limit);
    } else {
        size_t padding_size = limit - text.length();
        std::string padding(padding_size, char_str[0]);
        return text + padding;
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("tqzym"), (5), ("c")) == ("tqzym"));
}
