#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::istringstream iss(text);
    std::vector<std::string> arr;
    std::string word;
    while (iss >> word) {
        arr.push_back(word);
    }

    std::vector<std::string> result;
    for (const auto& item : arr) {
        if (item.find("day") != std::string::npos && item.find("day") == item.size() - 3) {
            result.push_back(item + 'y');
        } else {
            result.push_back(item + "day");
        }
    }

    std::string final_result;
    for (const auto& item : result) {
        final_result += item + " ";
    }
    final_result.pop_back(); // remove the extra space at the end
    return final_result;
}
int main() {
    auto candidate = f;
    assert(candidate(("nwv mef ofme bdryl")) == ("nwvday mefday ofmeday bdrylday"));
}
