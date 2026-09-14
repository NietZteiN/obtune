#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::istringstream iss(text);
    std::string word;
    while (iss >> word) {
        text = std::regex_replace(text, std::regex("-" + word), " ");
        text = std::regex_replace(text, std::regex(word + "-"), " ");
    }
    text.erase(0, text.find_first_not_of('-'));
    text.erase(text.find_last_not_of('-') + 1);
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("-stew---corn-and-beans-in soup-.-")) == ("stew---corn-and-beans-in soup-."));
}
