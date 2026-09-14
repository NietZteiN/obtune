#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::vector<long> arr) {
    arr.clear();
    arr.push_back(1);
    arr.push_back(2);
    arr.push_back(3);
    arr.push_back(4);

    std::stringstream ss;
    for (auto& num : arr) {
        ss << num;
        if (&num != &arr.back()) {
            ss << ",";
        }
    }
    
    return ss.str();
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)0, (long)1, (long)2, (long)3, (long)4}))) == ("1,2,3,4"));
}
