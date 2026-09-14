#include<assert.h>
#include<bits/stdc++.h>
union Union_long_std_string{
    long f0;
    std::string f1;    Union_long_std_string(long _f0) : f0(_f0) {}
    Union_long_std_string(std::string _f1) : f1(_f1) {}
    ~Union_long_std_string() {}
    bool operator==(long f) {
        return f0 == f ;
    }    bool operator==(std::string f) {
        return f1 == f ;
    }
};
Union_long_std_string f(std::string ans) {
    if (std::all_of(ans.begin(), ans.end(), ::isdigit)) {
        int total = std::stoi(ans) * 4 - 50;
        total -= std::count_if(ans.begin(), ans.end(), [](char c) { return c != '0' && c != '2' && c != '4' && c != '6' && c != '8'; }) * 100;
        return total;
    }
    return Union_long_std_string("NAN");
}
int main() {
    auto candidate = f;
    assert(candidate(("0")) == -50);
}
