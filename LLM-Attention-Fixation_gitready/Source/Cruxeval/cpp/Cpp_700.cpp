#include<assert.h>
#include<bits/stdc++.h>
long f(std::string text) {
    std::string needle = "bot";
    long count = 0;
    for (size_t off = 0; (off = text.find(needle, off)) != std::string::npos; ++count, ++off);
    return text.length() - count;
}
int main() {
    auto candidate = f;
    assert(candidate(("Where is the bot in this world?")) == (30));
}
