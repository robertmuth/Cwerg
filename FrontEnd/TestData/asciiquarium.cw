@doc "main module with program entry point `main`"
(module main [] :
(import ./ascii_artwork artwork)
(import ./ascii_anim aanim)
(import ansi)
(import os)
(import fmt)

(global @mut all_objects auto (array_val 100 aanim::ObjectState))


(fun @cdecl main [(param argc s32) (param argv (ptr (ptr u8)))] s32 :
    (if (< argc 3) :
        (fmt::print! "Not enough arguments, need width and height\n")
        (return 0)
        :)
    (let arg_w (slice u8) (fmt::strz_to_slice [(^ (&+ argv 1))]))
    (let arg_h (slice u8) (fmt::strz_to_slice [(^ (&+ argv 2))]))
    (let width s32 (as (fmt::str_to_u32 [arg_w]) s32))
    (let height s32 (as (fmt::str_to_u32 [arg_h]) s32))
    @doc "100ms per frame"
    (let @ref req os::TimeSpec (rec_val os::TimeSpec [(field_val 0) (field_val 100000000)]))
    (let @mut @ref rem os::TimeSpec undef)
    (let @mut @ref window auto (rec_val aanim::Window [
        (field_val width)
        (field_val height)
        (field_val undef)
        (field_val undef)
        (field_val undef)
        ]))
    (let @mut curr auto (front @mut all_objects))
    @doc "add obj"
    (shed (aanim::InitObjectState [curr (& artwork::DuckR)]))
    (shed (aanim::SetBasics [
            curr
            0.0
            0
            5]))
    (= curr (&+ curr 1))
    @doc "add obj"

    (shed (aanim::InitObjectState [curr (& artwork::Castle)]))
    (shed (aanim::SetBasics [
            curr
            0.0
            (- (as width r32) 32)
            (- (as height r32) 13)]))
    (= curr (&+ curr 1))
    @doc "add obj"
    (shed (aanim::InitObjectState [curr (& artwork::BigFishR)]))
    (shed (aanim::SetBasics [
            curr
            0.0
            10
            10]))
    (= curr (&+ curr 1))
    @doc "add obj"
    (shed (aanim::InitObjectState [curr (& artwork::SwanL)]))
    (shed (aanim::SetBasics [
            curr
            0.0
            50
            1]))
    (= curr (&+ curr 1))
    @doc "add obj"
    (shed (aanim::InitObjectState [curr (& artwork::DolphinL)]))
    (shed (aanim::SetBasics [
            curr
            0.0
            30
            8]))
    (= curr (&+ curr 1))
    @doc "add obj"
    (shed (aanim::InitObjectState [curr (& artwork::MonsterR)]))
    (shed (aanim::SetBasics [
            curr
            0.0
            30
            2]))
    (= curr (&+ curr 1))
    @doc "add obj"
    (shed (aanim::InitObjectState [curr (& artwork::SharkR)]))
    (shed (aanim::SetBasics [
            curr
            0.0
            30
            30]))
    (= curr (&+ curr 1))
    @doc "add obj"
    (shed (aanim::InitObjectState [curr (& artwork::ShipR)]))
    (shed (aanim::SetBasics [
            curr
            0.0
            50
            0]))
    (= curr (&+ curr 1))
    @doc "add obj"
    (shed (aanim::InitObjectState [curr (& artwork::Fish1R)]))
    (shed (aanim::SetBasics [
            curr
            0.0
            40
            40]))
    (= curr (&+ curr 1))
    @doc "add obj"
    (fmt::print! ansi::CURSOR_HIDE)
    (let @mut last_t r32 0.0)
    (for t 0.0 5.0_r32 0.1 :
        (shed (aanim::window_fill [
                (& @mut window)
                ' '
                ' ']))
        (= curr (front @mut all_objects))
        (for i 0 9_uint 1 :
            (shed (aanim::draw [(& @mut window) (&+ curr i)])))
        (shed (aanim::window_draw [(& window) 'k']))
        (for i 0 9_uint 1 :
            (shed (artwork::UpdateState [
                    (&+ curr i)
                    t
                    (- t last_t)])))
        (shed (os::nanosleep [(& req) (& @mut rem)]))
        (= last_t t))
    (fmt::print! ansi::CURSOR_SHOW)
    (return 0))


)
