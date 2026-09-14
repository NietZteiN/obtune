#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::string result = "";
    std::string punctuations = "!.?,:;";
    
    for (char punct : punctuations) {
        if (std::count(text.begin(), text.end(), punct) > 1) {
            return "no";
        }
        if (text.back() == punct) {
            return "no";
        }
    }
    
    std::string titleText = text;
    titleText[0] = std::toupper(titleText[0]);
    for (int i = 1; i < titleText.size(); ++i) {
        if (std::isspace(titleText[i - 1])) {
            titleText[i] = std::toupper(titleText[i]);
        } else {
            titleText[i] = std::tolower(titleText[i]);
        }
    }
    
    return titleText;
}
int main() {
    auto candidate = f;
    assert(candidate(("djhasghasgdha")) == ("Djhasghasgdha"));
}
