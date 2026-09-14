#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string fill, long size) {
    if (size < 0) {
        size = -size;
    }
    if (text.length() > size) {
        return text.substr(text.length() - size);
    }
    return text.insert(0, size - text.length(), fill[0]);
}
int main() {
    auto candidate = f;
    assert(candidate(("no asw"), ("j"), (1)) == ("w"));
}
