#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string value) {
    int length = text.length();
    int index = 0;
    while (length > 0) {
        value = text[index] + value;
        length--;
        index++;
    }
    return value;
}
int main() {
    auto candidate = f;
    assert(candidate(("jao mt"), ("house")) == ("tm oajhouse"));
}
