#include<assert.h>
#include<bits/stdc++.h>
std::tuple<long, std::string> f(std::string text, std::string lower, std::string upper) {
    long count = 0;
    std::string new_text = "";
    for (char& char_ : text) {
        if (isdigit(char_)) {
            char_ = lower[0];
        } else {
            char_ = upper[0];
        }
        if (char_ == 'p' || char_ == 'C') {
            count += 1;
        }
        new_text += char_;
    }
    return std::make_tuple(count, new_text);
}
int main() {
    auto candidate = f;
    assert(candidate(("DSUWeqExTQdCMGpqur"), ("a"), ("x")) == (std::make_tuple(0, "xxxxxxxxxxxxxxxxxx")));
}
