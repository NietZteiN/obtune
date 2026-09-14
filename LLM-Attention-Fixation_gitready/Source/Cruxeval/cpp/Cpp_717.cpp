#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    int k = 0, l = text.length() - 1;
    while (!isalpha(text[l])) {
        l--;
    }
    while (!isalpha(text[k])) {
        k++;
    }
    if (k != 0 || l != text.length() - 1) {
        return text.substr(k, l - k + 1);
    } else {
        return text.substr(0, 1);
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("timetable, 2mil")) == ("t"));
}
