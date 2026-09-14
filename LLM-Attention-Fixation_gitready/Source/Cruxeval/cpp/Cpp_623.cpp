#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::vector<std::string> rules) {
    for (std::string rule : rules) {
        if (rule == "@") {
            std::reverse(text.begin(), text.end());
        } else if (rule == "~") {
            std::transform(text.begin(), text.end(), text.begin(), ::toupper);
        } else if (!text.empty() && text.back() == rule[0]) {
            text.pop_back();
        }
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("hi~!"), (std::vector<std::string>({(std::string)"~", (std::string)"`", (std::string)"!", (std::string)"&"}))) == ("HI~"));
}
