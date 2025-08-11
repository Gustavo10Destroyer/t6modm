on_game_started()
{
    level endon("end_game");

    level waittill("initial_blackscreen_passed");
    scripts\zm\test::info(&"MESSAGE_T6MODM");
}

init()
{
    precacheshader("my_shader");
    precachestring(&"MESSAGE_T6MODM");

    elem = newhudelem();
    elem setshader("my_shader", 32, 32);

    thread on_game_started();
}