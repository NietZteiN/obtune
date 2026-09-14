#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, long position, std::string value) {
    int length = text.length();
    int index = position % length;
    if (position < 0) {
        index = length / 2;
    }
    text.insert(index, value);
    text.erase(length - 1, 1);
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("sduyai"), (1), ("y")) == ("syduyi"));
}
