#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, long position, std::string value) {
    int length = text.size();
    int index = (position % (length + 2)) - 1;
    if (index >= length || index < 0) {
        return text;
    }
    text[index] = value[0];
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("1zd"), (0), ("m")) == ("1zd"));
}
