#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::replace(text.begin(), text.end(), '\n', '\t');
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("apples\n	\npears\n	\nbananas")) == ("apples			pears			bananas"));
}
