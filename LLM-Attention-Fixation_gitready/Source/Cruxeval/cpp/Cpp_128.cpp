#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::string odd = "";
    std::string even = "";
    for (int i = 0; i < text.size(); i++) {
        if (i % 2 == 0) {
            even += text[i];
        } else {
            odd += text[i];
        }
    }
    std::transform(odd.begin(), odd.end(), odd.begin(), ::tolower);
    return even + odd;
}
int main() {
    auto candidate = f;
    assert(candidate(("Mammoth")) == ("Mmohamt"));
}
