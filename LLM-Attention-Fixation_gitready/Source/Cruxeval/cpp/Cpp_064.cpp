#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, long size) {
    long counter = text.length();
    for (long i = 0; i < size - (size % 2); ++i) {
        text = " " + text + " ";
        counter += 2;
        if (counter >= size) {
            return text;
        }
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("7"), (10)) == ("     7     "));
}
