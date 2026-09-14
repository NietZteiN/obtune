#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string to_place) {
    std::size_t pos = text.find(to_place);
    std::string after_place = text.substr(0, pos + 1);
    std::string before_place = text.substr(pos + 1);
    return after_place + before_place;
}
int main() {
    auto candidate = f;
    assert(candidate(("some text"), ("some")) == ("some text"));
}
